def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    self_cells = set(tuple(p) for p in observation.get("self_territory", []))
    opp_cells = set(tuple(p) for p in observation.get("opponent_territory", []))
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cell_is_edge(x, y): return x == 0 or y == 0 or x == w - 1 or y == h - 1

    my_front = min((abs(sx - x) + abs(sy - y) for (x, y) in opp_cells), default=99)
    best, bestv = (0, 0), -10**18

    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            v = -10**12
        else:
            # Features around landing cell
            adj_opp = 0
            adj_self = 0
            opp_near = 0
            for ddx, ddy in neigh8:
                px, py = nx + ddx, ny + ddy
                if inb(px, py) and (px, py) in opp_cells: adj_opp += 1
                if inb(px, py) and (px, py) in self_cells: adj_self += 1
                if inb(px, py) and (px, py) in opp_cells: opp_near = 1

            if (nx, ny) in self_cells:
                v = 2.2 + 0.15 * adj_self - 0.10 * adj_opp
            elif (nx, ny) in opp_cells:
                # Flipping into opponent territory: strong if it also breaks their edge pressure
                dist_edge = min(nx, ny, w - 1 - nx, h - 1 - ny)
                v = 35.0 + 1.2 * adj_opp - 0.6 * dist_edge - 0.15 * (abs(nx - ox) + abs(ny - oy))
            elif (nx, ny) in unclaimed:
                # Prefer unclaimed that is adjacent to their territory, but avoid feeding their edge expansion
                dist_to_opp = min((abs(nx - x) + abs(ny - y) for (x, y) in opp_cells), default=99)
                edge_pen = 9.0 if cell_is_edge(nx, ny) else 0.0
                v = 12.0 + 3.0 * adj_opp - 0.55 * dist_to_opp - edge_pen + 0.15 * adj_self
                # If we're far from their front, bias towards faster approach (inward, not hugging edges)
                if my_front > 8 and not cell_is_edge(nx, ny):
                    v += 2.0 - 0.05 * (abs(nx - ox) + abs(ny - oy))
            else:
                v = 0.0

            # Micro-avoidance: don't step onto squares that are "open" to their territory (low adj_self, high adj_opp)
            if (nx, ny) not in self_cells and adj_opp >= 2 and adj_self == 0:
                v -= 4.0

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]