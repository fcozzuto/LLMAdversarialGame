def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = {tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2}
    self_t = {tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2}
    opp_t = {tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2}
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    # Focus target: nearest good unclaimed; else push toward unclaimed; else avoid opponent territory
    target = None
    if unclaimed:
        ux, uy = sx, sy
        bestd = 10**9
        for x, y in unclaimed:
            if (x, y) in obstacles:
                continue
            d = abs(x - ux) + abs(y - uy)
            if d < bestd:
                bestd = d
                target = (x, y)

    best_move = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dcenter = abs(nx - cx) + abs(ny - cy)
        dopp = abs(nx - ox) + abs(ny - oy)

        v = 0.0
        if (nx, ny) in self_t:
            v += 80.0 - 1.8 * dcenter - 0.3 * dopp
            v += 1.0 / (1.0 + edge_dist(nx, ny))
        elif (nx, ny) in opp_t:
            # Flipping on entry: try to capture opponent area when close to them, but not recklessly
            v += 110.0 - 4.0 * dcenter - 0.8 * dopp + 0.8 / (1.0 + edge_dist(nx, ny))
            v -= 0.15 * (abs(nx - sx) + abs(ny - sy))
        else:
            # unclaimed or neutral
            v += 40.0 - 2.0 * dcenter - 0.2 * dopp
            v += 1.2 / (1.0 + edge_dist(nx, ny))
            if target is not None:
                v += -1.0 * (abs(nx - target[0]) + abs(ny - target[1]))
            else:
                # prefer staying away from opponent center pressure when no clear target
                v -= 0.25 * dopp

            # small bonus if adjacent to our territory (reduces fragmentation)
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    px, py = nx + ax, ny + ay
                    if inb(px, py) and (px, py) in self_t:
                        v += 3.0
                        break
                else:
                    continue
                break

        if v > bestv:
            bestv = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]