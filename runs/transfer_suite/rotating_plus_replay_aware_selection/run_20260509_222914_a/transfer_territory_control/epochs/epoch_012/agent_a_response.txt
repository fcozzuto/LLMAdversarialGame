def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    opp_neighbors = set()
    for (x, y) in opp_terr:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny):
                        opp_neighbors.add((nx, ny))

    candidates = []
    # Attack: prioritize unclaimed cells adjacent to opponent territory
    for c in unclaimed:
        if c in opp_neighbors and c not in obstacles:
            candidates.append(c)

    # Fallback: any unclaimed, but bias toward opponent side
    if not candidates:
        for c in unclaimed:
            if c not in obstacles:
                candidates.append(c)

    # If still nothing, just stay / move toward opponent
    if not candidates:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    def score_target(tx, ty):
        # Lower is better: closer and more "pressuring" (near opponent territory)
        d = abs(tx - sx) + abs(ty - sy)
        press = 0 if (tx, ty) in opp_neighbors else 6
        toward_opp = abs(ox - tx) + abs(oy - ty)
        # Secondary tie-breakers for determinism
        return (d + press, toward_opp, ty, tx)

    tx, ty = min(candidates, key=lambda c: score_target(c[0], c[1]))

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer moving closer to target; discourage leaving board via tie-breaks already handled
        dist = abs(tx - nx) + abs(ty - ny)
        # Attack bonus if stepping into opponent-owned territory region (flip enabled)
        step_press = 0 if (nx, ny) in opp_terr else 1
        # Deterministic tie-break
        val = (dist + 0.5 * step_press, abs(ox - nx) + abs(oy - ny), dy, dx)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move