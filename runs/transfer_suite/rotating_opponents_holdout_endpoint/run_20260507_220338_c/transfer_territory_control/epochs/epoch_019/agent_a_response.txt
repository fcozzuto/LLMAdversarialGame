def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    my = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    un = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not my:
        my = {(sx, sy)}

    # Prefer stepping into unclaimed, especially those that extend our frontier.
    frontier_targets = set()
    for x, y in my:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in un and (nx, ny) not in obstacles:
                frontier_targets.add((nx, ny))

    targets = frontier_targets if frontier_targets else un
    if not targets:
        # Fallback: move toward opponent position while avoiding obstacles.
        candidates = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((abs(nx - ox) + abs(ny - oy), nx, ny, dx, dy))
        candidates.sort()
        return [candidates[0][3], candidates[0][4]] if candidates else [0, 0]

    # Choose the move that best reduces distance to the best target, and avoids getting stuck.
    # Deterministic: compute candidate move score from nearest target distance + tie-break by coords.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # If next cell is unclaimed, strongly prefer it.
        dist_to_targets = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in targets)
        on_unclaimed = 1 if (nx, ny) in un else 0
        # Also nudge toward board center to keep mobility.
        center_nudge = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        score = (-10 * on_unclaimed, dist_to_targets, center_nudge, nx, ny, dx, dy)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]