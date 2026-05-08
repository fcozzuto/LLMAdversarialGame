def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    evader = ("evader" in role) and ("pursuer" not in role)
    if "pursuer" in role:
        evader = False

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def center_bias(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx = x - cx
        dy = y - cy
        return dx * dx + dy * dy

    best = None
    best_mv = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d = cheb(nx, ny, ox, oy)
        if not evader:
            # pursuer: win asap, then reduce distance, then prefer center
            if nx == ox and ny == oy:
                val = 10**9
            else:
                val = -(d * 1000 + int(center_bias(nx, ny)))
        else:
            # evader: avoid capture, then increase distance, then prefer center lightly
            if nx == ox and ny == oy:
                val = -10**9
            else:
                val = d * 1000 - int(center_bias(nx, ny) * 0.1)

        if best is None or val > best:
            best = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]