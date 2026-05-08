def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, -10**18)

    # Bias: contest the center and threaten immediate adjacency to opponent.
    # Also avoid obstacles and avoid stepping too deep into opponent territory unless it advances center-control.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - ox) + abs(ny - oy)
        in_unclaimed = 1 if (nx, ny) in unclaimed else 0
        in_self = 1 if (nx, ny) in self_terr else 0
        in_opp = 1 if (nx, ny) in opp_terr else 0

        # Deterrence/pressure terms
        adjacent_to_opp = 1 if d_opp == 1 else 0
        near_opportunity = 1 if d_opp <= 2 else 0

        # If we can expand into unclaimed, prefer it; if opponent-owned, only do so when also strong center progress.
        score = 0
        score += (20.0 - 2.5 * d_center)  # central claim priority
        score += 12.0 * in_unclaimed
        score += 2.0 * in_self
        score += 8.0 * adjacent_to_opp + 3.0 * near_opportunity
        score -= 14.0 * in_opp * (0.3 + d_center / (w + h))  # discourage deep opponent capture except near center
        score -= 3.0 * (d_opp == 0)  # avoid being on top (rare)

        # Deterministic tiebreak: prefer moves that reduce center distance, then reduce opp distance.
        tieb = (-d_center, -d_opp, dx, dy)
        if score > best[1] or (score == best[1] and best[0] is not None and tieb > best[2]):
            best = ((dx, dy), score, tieb)

    if best[0] is None:
        return [0, 0]
    dx, dy = best[0]
    return [int(dx), int(dy)]