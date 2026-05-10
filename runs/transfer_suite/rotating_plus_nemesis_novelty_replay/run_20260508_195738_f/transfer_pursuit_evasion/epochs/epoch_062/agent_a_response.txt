def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx, dy = abs(x - ox), abs(y - oy)
        return dx if dx > dy else dy

    best = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        d = cheb(nx, ny)
        if not self_is_evader:
            if nx == ox and ny == oy:
                key = (0, 0, 0)
            else:
                min_obst = 10
                for bx, by in obs:
                    dd = abs(nx - bx) + abs(ny - by)
                    if dd < min_obst:
                        min_obst = dd
                # Primary: minimize distance to opponent; Secondary: stay away from obstacles; Tertiary: tie-break to deterministic preference
                key = (d, -min_obst, (-(nx + ny)))
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        else:
            # Evader: maximize distance to opponent; also avoid obstacles and opponent proximity
            min_obst = 10
            for bx, by in obs:
                dd = abs(nx - bx) + abs(ny - by)
                if dd < min_obst:
                    min_obst = dd
            opp_prox = abs(nx - ox) + abs(ny - oy)
            # capture ends game; avoid getting adjacent if possible (capture requires same cell)
            key = (-d, -(min_obst), -opp_prox, (nx + 3 * ny))
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]