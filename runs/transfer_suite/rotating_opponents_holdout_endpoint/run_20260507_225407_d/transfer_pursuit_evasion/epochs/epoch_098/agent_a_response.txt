def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role") or "")
    self_lower = self_role.lower()
    we_pursuer = ("pursuer" in self_lower) or ("pursue" in self_lower and "evader" not in self_lower)
    # If ambiguous, default to pursuer-like chase (better under pursuit evasion setups)
    we_evader = not we_pursuer

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()  # deterministic tie-break

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Prefer not to "bounce" into boundaries/obstacles by modeling invalid moves as staying put.
    best_move = deltas[0]
    if we_pursuer:
        best_score = 10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            dist = cheb(nx, ny, ox, oy)
            # Greedy chase with mild "path openness" bias to avoid getting stuck at walls
            open_cnt = 0
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if free(tx, ty):
                    open_cnt += 1
            score = dist * 100 - open_cnt
            if score < best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        best_score = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            dist = cheb(nx, ny, ox, oy)
            # Prefer distance first; then prefer moves with more freedom to counter wall-run traps
            open_cnt = 0
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if free(tx, ty):
                    open_cnt += 1
            # Also lightly discourage moving closer in Manhattan
            man_close = abs(nx - ox) + abs(ny - oy)
            score = dist * 1000 + open_cnt * 10 - man_close
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]