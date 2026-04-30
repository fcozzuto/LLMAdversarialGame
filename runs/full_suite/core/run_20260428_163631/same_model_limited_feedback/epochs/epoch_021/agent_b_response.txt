def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh_steps():
        steps = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                steps.append((dx, dy))
        steps.append((0, 0))
        return steps

    def best_target():
        if not resources:
            return None
        best = None
        best_val = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d1 = abs(rx - sx) + abs(ry - sy)
            d2 = abs(rx - ox) + abs(ry - oy)
            # Prefer resources where we are closer; slight preference for nearer overall.
            val = (d2 - d1) * 10 - d1
            # Small bias toward center to break ties deterministically.
            val += - (abs(rx - cx) + abs(ry - cy)) * 0.01
            if val > best_val:
                best_val = val
                best = (rx, ry)
        return best

    target = best_target()

    steps = neigh_steps()
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if target is None:
            # If no resources, head toward opponent cautiously (deterministic center bias).
            tx, ty = ox, oy
        else:
            tx, ty = target[0], target[1]

        myd = abs(tx - nx) + abs(ty - ny)
        curd = abs(tx - sx) + abs(ty - sy)

        # Prefer reducing distance to target; if equal, prefer moving toward center.
        score = (curd - myd) * 100
        score += -myd
        score += - (abs(nx - cx) + abs(ny - cy)) * 0.1

        # Avoid stepping into positions that are simultaneously adjacent to opponent target pursuit.
        # (Lightweight deterrent: if opponent can reach current cell in 1, slightly penalize.)
        opp_to_cell = abs(nx - ox) + abs(ny - oy)
        score += -5 if opp_to_cell <= 2 else 0

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]