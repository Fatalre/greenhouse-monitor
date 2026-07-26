import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricCard } from "../components/MetricCard";
import { StatusBadge } from "../components/StatusBadge";

describe("UI smoke", () => {
  it("renders null values", () => {
    render(<MetricCard title="TC1" value={null} unit="°C"/>);
    expect(screen.getByText("Нет данных")).toBeInTheDocument();
  });
  it("renders status", () => {
    render(<StatusBadge status="ok" label="Online"/>);
    expect(screen.getByText("Online")).toBeInTheDocument();
  });
});
