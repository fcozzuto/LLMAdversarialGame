def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass

    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dist_opp = abs(nx - ox) + abs(ny - oy)
        center_pref = -int((abs(nx - cx) + abs(ny - cy)) * 2)  # closer to center is better

        if (nx, ny) in opp_set:
            flip_bonus = 6
        elif (nx, ny) in unclaimed:
            flip_bonus = 4
        elif (nx, ny) in self_set:
            flip_bonus = 1
        else:
            flip_bonus = 0

        # Frontier push: prefer cells adjacent to our territory (expansion / reinforcement)
        neigh_self = False
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in self_set:
                    neigh_self = True
                    break
            if neigh_self:
                break
        frontier = 3 if neigh_self else 0

        score = (-2 * dist_opp) + center_pref + flip_bonus + frontier
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best