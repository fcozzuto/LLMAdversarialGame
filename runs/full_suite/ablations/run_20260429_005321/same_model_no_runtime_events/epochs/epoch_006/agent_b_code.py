def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return max(abs(a - c), abs(b - d))  # Chebyshev

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    any_res = False
    for rx, ry in resources:
        if (rx, ry) not in obstacles:
            any_res = True
            break

    for dx, dy, nx, ny in legal:
        if any_res:
            my_best = -10**18
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                dm = dist(nx, ny, rx, ry)
                do = dist(ox, oy, rx, ry)
                # Prefer resources where we arrive earlier; heavily penalize those opponent can take first.
                adv = do - dm
                # Also mildly prefer resources that are far from opponent (after they potentially get there).
                far_from_opp = -dist(rx, ry, w - 1 - ox, h - 1 - oy)
                # If tie on arrival time, prefer closer-to-self next.
                tie = -dm
                score = adv * 100 - dm * 2 + far_from_opp + tie * 0.5
                if score > my_best:
                    my_best = score
            # Add safety: avoid moves that let opponent instantly reach our position neighborhood.
            opp_reach_here = dist(ox, oy, nx, ny)
            safety = -opp_reach_here * 0.25
            val = my_best + safety
        else:
            # No visible resources: move to maximize distance from opponent while drifting toward center.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            val = dist(nx, ny, ox, oy) * 2 - dist(nx, ny, cx, cy) * 0.1

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]