def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    center_x, center_y = w // 2, h // 2
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dist_to_center = abs(nx - center_x) + abs(ny - center_y)
        dist_to_opp = abs(nx - ox) + abs(ny - oy)

        if (nx, ny) in opp_terr:
            val = 10**6 + 1000 - dist_to_opp
        elif (nx, ny) in unclaimed:
            val = 20000 - dist_to_center
        else:
            # prefer edging expansion: move towards nearest unclaimed if possible
            if unclaimed:
                # deterministic nearest: break ties by (x,y)
                tx, ty = min(unclaimed, key=lambda c: (abs(c[0] - nx) + abs(c[1] - ny), c[0], c[1]))
                val = 1000 - (abs(tx - nx) + abs(ty - ny)) - 0.01 * dist_to_center
            else:
                val = -dist_to_center - 0.01 * dist_to_opp

            # slightly reduce probability of walking away from opponent territory
            val += 0.05 * (abs(sx - ox) + abs(sy - oy) - dist_to_opp)

        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    # If all moves blocked/invalid, stay
    return [int(best[0]), int(best[1])]