def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = sorted(dirs, key=lambda t: (t[0], t[1]))  # deterministic tie-break

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    if is_evader:
        best_val = -1
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            # Encourage cornering deterministically as secondary objective.
            corner_d = max(cheb(cx, cy, nx, ny) for cx, cy in corners)
            val = (d, corner_d)
            if val > best_val if isinstance(best_val, tuple) else False:
                best_val = val
                best_move = (dx, dy)
            elif isinstance(best_val, tuple) and val == best_val:
                best_move = (dx, dy)
        if best_val == -1:
            return [0, 0]
        return [best_move[0], best_move[1]]
    else:
        best_dist = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            if dist < best_dist:
                best_dist = dist
                best_move = (dx, dy)
        if best_dist == 10**9:
            return [0, 0]
        return [best_move[0], best_move[1]]