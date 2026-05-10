def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "pursuer").lower()
    pursuer = (role != "evader")

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    # Tie-breaker order: prefer staying still less often unless it is best.
    def tie_key(dx, dy):
        return (0 if (dx, dy) == (0, 0) else 1, abs(dx) + abs(dy), dx, dy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = max(abs(nx - ox), abs(ny - oy))  # capture at exact position when radius=0
        # If pursuer: minimize dist; if evader: maximize dist.
        score = dist if pursuer else -dist
        if best_score is None or (score < best_score if pursuer else score > best_score):
            best_score = score
            best = (dx, dy)
        elif best is not None:
            better = (score < best_score) if pursuer else (score > best_score)
            equal = score == best_score
            if equal and better is False:
                # Deterministic tie-break
                if tie_key(dx, dy) < tie_key(best[0], best[1]):
                    best = (dx, dy)

    if best is not None:
        return [int(best[0]), int(best[1])]

    # Fallback: deterministic move that stays in-bounds (engine would keep in place if invalid)
    # Here we choose a direct step without considering obstacles.
    dx = 0 if ox == sx else (1 if ox > sx else -1)
    dy = 0 if oy == sy else (1 if oy > sy else -1)
    if not (0 <= sx + dx < w and 0 <= sy + dy < h):
        dx = 0
    if not (0 <= sx + dx < w and 0 <= sy + dy < h):
        dy = 0
    return [int(dx), int(dy)] if pursuer else [int(-dx), int(-dy)]