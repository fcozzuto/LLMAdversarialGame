def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for it in observation.get("obstacles", []) or []:
        if it is None:
            continue
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursue" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def score_pursuer(nx, ny):
        d = max(abs(nx - ox), abs(ny - oy))  # Chebyshev aligns with diagonal moves
        return (d, abs(nx - sx) + abs(ny - sy))

    def score_evader(nx, ny):
        d = max(abs(nx - ox), abs(ny - oy))
        cen = max(abs(nx - (w - 1) / 2.0), abs(ny - (h - 1) / 2.0))
        return (-d, -cen)  # maximize distance; tie-break toward edges (centering helps deterministic bias)

    best = (10**9, 10**9)
    best_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s = score_pursuer(nx, ny) if i_am_pursuer else score_evader(nx, ny)
        if s < best:
            best = s
            best_moves = [(dx, dy)]
        elif s == best:
            best_moves.append((dx, dy))

    # Deterministic tie-break: prefer moves with smaller dx, then smaller dy, then staying still
    best_moves.sort(key=lambda m: (abs(m[0]), abs(m[1]), 0 if (m[0] == 0 and m[1] == 0) else 1))
    return [best_moves[0][0], best_moves[0][1]]