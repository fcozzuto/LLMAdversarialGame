def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles if p is not None and len(p) == 2}
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_move_for(pos):
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            dx = 0 if cx == pos[0] else (1 if cx > pos[0] else -1)
            dy = 0 if cy == pos[1] else (1 if cy > pos[1] else -1)
            if (pos[0] + dx, pos[1] + dy) in obs:
                if (pos[0] + dx, pos[1]) not in obs and inb(pos[0] + dx, pos[1]):
                    return (dx, 0)
                if (pos[0], pos[1] + dy) not in obs and inb(pos[0], pos[1] + dy):
                    return (0, dy)
                return (0, 0)
            return (dx, dy)

        my = pos
        best_adv = None
        best_dme = None
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obs:
                continue
            d_me = cheb(my, (rx, ry))
            d_op = cheb((ox, oy), (rx, ry))
            adv = d_me - d_op  # negative is good (we closer)
            key = (adv, d_me, rx, ry)
            if best_adv is None or key < (best_adv, best_dme, 0, 0):
                best_adv = adv
                best_dme = d_me
        # If we have some resources, return best direction that improves (adv, d_me)
        best_key = None
        best_delta = (0, 0)
        for dx, dy in dirs:
            nx, ny = my[0] + dx, my[1] + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            if not resources:
                continue
            cand_best_adv = None
            cand_best_dme = None
            for r in resources:
                rx, ry = r[0], r[1]
                if (rx, ry) in obs:
                    continue
                d_me = cheb((nx, ny), (rx, ry))
                d_op = cheb((ox, oy), (rx, ry))
                adv = d_me - d_op
                key = (adv, d_me, rx, ry)
                if cand_best_adv is None or key < (cand_best_adv, cand_best_dme, 0, 0):
                    cand_best_adv = adv
                    cand_best_dme = d_me
            # maximize advantage -> minimize (adv, d_me) (since adv is negative when good)
            val_key = (cand_best_adv, cand_best_dme, nx, ny)
            if best_key is None or val_key < best_key:
                best_key = val_key
                best_delta = (dx, dy)
        return best_delta

    dx, dy = best_move_for((sx, sy))
    return [int(dx), int(dy)]