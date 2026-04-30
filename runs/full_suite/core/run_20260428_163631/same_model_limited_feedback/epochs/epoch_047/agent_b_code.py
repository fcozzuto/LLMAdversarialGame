def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_step(tx, ty):
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            ds = dist((nx, ny), (tx, ty))
            # Prefer closer to target; break ties by moving toward opponent's distance delta
            key = (ds, abs((dist((sx, sy), (tx, ty)) - dist((ox, oy), (tx, ty)))) - abs((dist((nx, ny), (tx, ty)) - dist((ox, oy), (tx, ty)))),
                   abs(nx - ox) + abs(ny - oy))
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        if best is None:
            # All blocked; allow staying
            return [0, 0]
        return [best[0], best[1]]

    if resources:
        # Strategic change: target resources where we have the biggest distance advantage over opponent.
        best_r = None
        best_adv = None
        best_selfd = None
        for r in resources:
            rd = tuple(r)
            sd = dist((sx, sy), rd)
            od = dist((ox, oy), rd)
            adv = od - sd  # higher means we're closer
            if best_r is None or (adv > best_adv) or (adv == best_adv and (sd < best_selfd)):
                best_r = rd
                best_adv = adv
                best_selfd = sd
        return best_step(best_r[0], best_r[1])

    # No resources visible: drift toward center while avoiding obstacles.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    return best_step(cx, cy)