def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evader = ("evader" in self_role) and ("evader" not in opp_role)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    # Deterministic tie-break order already in moves list; use strict comparisons only.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy

        # Additional penalty for being adjacent to obstacles (both roles)
        adj = 0
        for ax, ay in obstacles:
            rdx, rdy = ax - nx, ay - ny
            if rdx * rdx + rdy * rdy == 1:
                adj += 1

        # Evader: maximize distance; Pursuer: minimize distance
        score = d2 - 3 * adj if evader else -d2 - 3 * adj

        # Small deterministic preference to avoid staying still if not optimal
        if dx == 0 and dy == 0:
            score -= 0.01

        if best is None or (score > best_score if evader else score > best_score):
            best = (dx, dy)
            best_score = score

    # If all moves blocked, stay
    if best is None:
        return [0, 0]
    return [best[0], best[1]]