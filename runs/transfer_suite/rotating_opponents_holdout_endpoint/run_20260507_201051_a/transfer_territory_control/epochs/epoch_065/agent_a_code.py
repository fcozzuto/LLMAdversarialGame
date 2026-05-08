def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obs_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def sign(a): return (a > 0) - (a < 0)

    self_cells = set()
    for p in (observation.get("self_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_cells.add((int(p[0]), int(p[1])))
    opp_cells = set()
    for p in (observation.get("opponent_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_cells.add((int(p[0]), int(p[1])))
    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    # Move away from opponent while expanding into unclaimed/opponent cells.
    away_x = sign(sx - ox)
    away_y = sign(sy - oy)

    candidates = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    best = None
    best_score = None
    for dx, dy in candidates:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        on_border = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        if on_border:
            score += 4

        if (nx, ny) in self_cells:
            score += 2
        if (nx, ny) in unclaimed:
            score += 6
        if (nx, ny) in opp_cells:
            score += 4  # flipping on entry

        # Prefer progress away from opponent.
        score += 2 * (dx * away_x + dy * away_y)

        # Encourage moving closer to a border cell on our favored side.
        corner_bias = abs((nx - (w - 1 if away_x > 0 else 0))) + abs((ny - (h - 1 if away_y > 0 else 0)))
        score -= int(corner_bias * 0.01)

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]