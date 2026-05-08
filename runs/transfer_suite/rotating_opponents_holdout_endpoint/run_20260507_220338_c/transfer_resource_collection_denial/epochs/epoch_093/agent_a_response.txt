def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))
    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    tr = int(observation.get("turns_remaining", 0))
    risk = 1 if tr <= 4 else 0  # endgame: prioritize winning a race
    best_target = None
    best_val = None
    for rx, ry in resources:
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Prefer resource where we are closer than opponent (race), tie-break by shorter self distance.
        val = (opp_d - self_d, -self_d)
        if best_val is None or val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Move that improves race; also slightly avoids stepping away from nearest other resources.
        main = (opp_d - self_d)
        aux = 0
        if len(resources) > 1:
            md = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < md:
                    md = d
            aux = -md
        score = (main + risk, aux)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]