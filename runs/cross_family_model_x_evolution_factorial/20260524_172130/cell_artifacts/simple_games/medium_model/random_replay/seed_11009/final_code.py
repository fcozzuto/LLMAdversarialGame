def choose_move(observation):
    # Deterministic, robust movement using defensive access patterns.
    # Move toward the average position of observed points (resources, agents, territories),
    # otherwise toward origin, with deltas clamped to -1,0,1.

    def clamp1(v):
        if v > 0:
            return 1
        if v < 0:
            return -1
        return 0

    center_x = 0.0
    center_y = 0.0
    count = 0

    obs = observation if isinstance(observation, dict) else {}

    # Collect candidate points from a variety of possible keys
    def accumulate_points(points):
        nonlocal center_x, center_y, count
        if not points:
            return
        for p in points:
            if isinstance(p, dict):
                x = p.get("x", 0)
                y = p.get("y", 0)
            elif isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
            else:
                continue
            center_x += x
            center_y += y
            count += 1

    resources = obs.get("resources")
    accumulate_points(resources)

    agents = obs.get("agents")
    accumulate_points(agents)

    territories = obs.get("territories")
    accumulate_points(territories)

    if count > 0:
        center_x /= count
        center_y /= count
        ox = obs.get("x", 0)
        oy = obs.get("y", 0)
        dx = clamp1(center_x - ox)
        dy = clamp1(center_y - oy)
        return [dx, dy]

    # Fallback: use a preferred_move hint if available
    ox = obs.get("x", 0)
    oy = obs.get("y", 0)
    preferred = obs.get("preferred_move")
    if isinstance(preferred, (list, tuple)) and len(preferred) >= 2:
        dx = clamp1(preferred[0] - ox)
        dy = clamp1(preferred[1] - oy)
        return [dx, dy]

    # Last resort: move toward origin
    dx = clamp1(-ox)
    dy = clamp1(-oy)
    return [dx, dy]
