def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_obj = 10**18

    cx, cy = w // 2, h // 2
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if resources:
            local_best_adv = None
            local_best_ds = None
            for x, y in resources:
                ds = cheb(nx, ny, x, y)
                do = cheb(ox, oy, x, y)
                adv = ds - do  # negative is good for us
                if local_best_adv is None or adv < local_best_adv or (adv == local_best_adv and ds < local_best_ds):
                    local_best_adv = adv
                    local_best_ds = ds

            # Prefer resources where we're closer than opponent; also keep progress toward center slightly.
            obj = (local_best_adv * 10) + (local_best_ds) + (cheb(nx, ny, ox, oy) * 0.03)
            obj += (cheb(nx, ny, cx, cy) * 0.002)
        else:
            # No visible resources: move toward center and away from opponent a bit.
            obj = cheb(nx, ny, cx, cy) * 1.0 + cheb(nx, ny, ox, oy) * 0.1

        if obj < best_obj:
            best_obj = obj
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]