def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    sr = (observation.get("self_role", "") or "").lower()
    flee = ("evader" in sr) or ("runner" in sr) or ("evade" in sr)

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neighbors_free_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                c += 1
        return c

    best_move = (0, 0)
    best_score = None

    # tie-break order deterministic: iterate fixed move list; higher preferred if pursuer->minimize distance => maximize score
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d = abs(nx - ox) + abs(ny - oy)
        towards = (1 if (dx != 0 or dy != 0) else 0)
        # dot-like towards opponent using sign of delta
        signx = 0 if ox == sx else (1 if ox > sx else -1)
        signy = 0 if oy == sy else (1 if oy > sy else -1)
        dir_toward = (1 if (dx == signx or dx == 0) and (dy == signy or dy == 0) else 0)

        mob = neighbors_free_count(nx, ny)

        if flee:
            # Prefer larger distance, keep mobility, and avoid corners/walls traps
            score = (d * 4) + (mob * 1.2) + (dir_toward * 0.2)
            # discourage stepping into low-mobility squares when fleeing
            if mob <= 2:
                score -= 2.5
        else:
            # Prefer smaller distance; if similar, force direction toward opponent; avoid giving opponent escape by reducing our mobility
            score = (-d * 4) + (dir_toward * 1.5) + (mob * 0.2)
            # discourage moves that are "sideways" against the chase when opponent is not aligned
            if not (dx == 0 or dy == 0) and (abs(ox - sx) != abs(oy - sy)):
                score -= 0.15

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]