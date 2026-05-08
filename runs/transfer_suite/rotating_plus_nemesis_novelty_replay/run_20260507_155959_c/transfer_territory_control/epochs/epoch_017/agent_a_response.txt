def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    ox, oy = (observation.get("opponent_position", [w - 1, h - 1]) + [w - 1, h - 1])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(xy) for xy in (observation.get("unclaimed_cells", []) or []))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    if opp_cells:
        ax = sum(x for x, _ in opp_cells) // len(opp_cells)
        ay = sum(y for _, y in opp_cells) // len(opp_cells)
    else:
        ax, ay = ox, oy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_val = -10**9

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_cells:
            val = 120
        elif (nx, ny) in unclaimed:
            val = 60
        elif (nx, ny) in self_cells:
            val = 10
        else:
            val = 20

        # Push into the center while keeping distance from opponent's claimed core.
        d_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - ax) + abs(ny - ay)
        val += int(30 - 2 * d_center)
        val += int(d_opp * 0.5)

        # If unclaimed exist, prefer moves that reduce distance to nearest unclaimed.
        if unclaimed:
            best_local = 10**9
            for ux, uy in unclaimed:
                dd = abs(nx - ux) + abs(ny - uy)
                if dd < best_local:
                    best_local = dd
                    if best_local == 0:
                        break
            val += int(25 - 2 * best_local)

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]