def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    best = None
    bestv = -10**18

    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            if (nx, ny) in opp_terr:
                cellv = 6.0
                risk = 0.25 * ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)) ** 0.5
                # When attacking, still prefer reducing distance to opponent's territory hotspots.
                seek = -0.02 * risk
            elif (nx, ny) in unclaimed:
                cellv = 3.2
                seek = -0.10 * (((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) ** 0.5)
            elif (nx, ny) in self_terr:
                cellv = 1.1
                seek = -0.01 * (((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) ** 0.5)
            else:
                cellv = 0.2
                seek = -0.02 * (((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) ** 0.5)

            # Edge-biased / center-avoidance to counter center-claim archetype
            dist_center = ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) ** 0.5
            edge_bias = 0.12 * dist_center
            # Maintain some distance from opponent unless directly attacking
            dist_opp = ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)) ** 0.5
            avoid = -0.08 * dist_opp if (nx, ny) not in opp_terr else 0.02 * dist_opp

            v = cellv + seek + edge_bias + avoid
            if v > bestv:
                bestv = v
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]