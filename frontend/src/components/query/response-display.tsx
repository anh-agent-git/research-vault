"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { QueryResponse, SourceReference } from "@/types";
import { ChevronDown, ChevronUp, ExternalLink } from "lucide-react";
import { Fragment, useMemo, useState } from "react";

export interface ResponseDisplayProps {
  response: QueryResponse;
  onFollowUp?: (suggestion: string) => void;
}

const CONFIDENCE_VARIANTS: Record<string, "default" | "success" | "warning" | "secondary"> = {
  high: "success",
  medium: "warning",
  low: "secondary",
};

export function ResponseDisplay({ response, onFollowUp }: ResponseDisplayProps) {
  const [showAllSources, setShowAllSources] = useState(false);

  // Parse [P:id] citations in the response text
  const parsedResponse = useMemo(() => {
    const citationPattern = /\[P:([^\]]+)\]/g;
    const parts: Array<{ type: "text" | "citation"; value: string }> = [];
    let lastIndex = 0;
    let match;

    while ((match = citationPattern.exec(response.response)) !== null) {
      // Add text before citation
      if (match.index > lastIndex) {
        parts.push({
          type: "text",
          value: response.response.slice(lastIndex, match.index),
        });
      }
      // Add citation
      parts.push({ type: "citation", value: match[1] });
      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < response.response.length) {
      parts.push({
        type: "text",
        value: response.response.slice(lastIndex),
      });
    }

    return parts;
  }, [response.response]);

  const visibleSources = showAllSources
    ? response.sources
    : response.sources.slice(0, 3);

  return (
    <div className="space-y-4">
      {/* Response text with parsed citations */}
      <div className="prose prose-sm max-w-none dark:prose-invert">
        {parsedResponse.map((part, i) =>
          part.type === "citation" ? (
            <CitationLink
              key={i}
              patternId={part.value}
              sources={response.sources}
              onExpand={() => setShowAllSources(true)}
            />
          ) : (
            <Fragment key={i}>{part.value}</Fragment>
          )
        )}
      </div>

      {/* Confidence badge */}
      {response.confidence && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Confidence:</span>
          <Badge variant={CONFIDENCE_VARIANTS[response.confidence] || "secondary"}>
            {response.confidence}
          </Badge>
        </div>
      )}

      {/* Sources */}
      {response.sources.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground">
            Sources ({response.sources.length})
          </h4>
          <div className="space-y-2">
            {visibleSources.map((source) => (
              <SourceCard key={source.pattern_id} source={source} />
            ))}
          </div>
          {response.sources.length > 3 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAllSources(!showAllSources)}
              className="w-full"
            >
              {showAllSources ? (
                <>
                  <ChevronUp className="h-4 w-4" />
                  Show less
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4" />
                  Show {response.sources.length - 3} more
                </>
              )}
            </Button>
          )}
        </div>
      )}

      {/* Follow-up suggestions */}
      {response.follow_up_suggestions && response.follow_up_suggestions.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground">
            Follow-up questions
          </h4>
          <div className="flex flex-wrap gap-2">
            {response.follow_up_suggestions.map((suggestion, i) => (
              <Button
                key={i}
                variant="outline"
                size="sm"
                onClick={() => onFollowUp?.(suggestion)}
                className="h-auto whitespace-normal text-left"
              >
                {suggestion}
              </Button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function CitationLink({
  patternId,
  sources,
  onExpand,
}: {
  patternId: string;
  sources: SourceReference[];
  onExpand?: () => void;
}) {
  const source = sources.find((s) => s.pattern_id === patternId);

  const handleClick = () => {
    // Expand sources if collapsed
    onExpand?.();

    // Scroll to the source card after a brief delay to allow expansion
    setTimeout(() => {
      const element = document.getElementById(`source-${patternId}`);
      if (element) {
        element.scrollIntoView({ behavior: "smooth", block: "center" });
        // Highlight briefly
        element.classList.add("ring-2", "ring-primary");
        setTimeout(() => {
          element.classList.remove("ring-2", "ring-primary");
        }, 2000);
      }
    }, 100);
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      className="inline-flex cursor-pointer items-center rounded bg-primary/10 px-1.5 py-0.5 text-xs font-medium text-primary hover:bg-primary/20 transition-colors"
      title={source?.summary || `Pattern ${patternId}`}
    >
      <ExternalLink className="mr-1 h-3 w-3" />
      {patternId.slice(0, 8)}
    </button>
  );
}

function SourceCard({ source }: { source: SourceReference }) {
  return (
    <Card id={`source-${source.pattern_id}`} className="bg-muted/50 transition-all">
      <CardContent className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-foreground">
              {source.pattern_id.slice(0, 8)}...
            </p>
            {source.summary && (
              <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                {source.summary}
              </p>
            )}
          </div>
          {source.relevance_score != null && (
            <Badge variant="outline" className="shrink-0">
              {Math.round(source.relevance_score * 100)}%
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
