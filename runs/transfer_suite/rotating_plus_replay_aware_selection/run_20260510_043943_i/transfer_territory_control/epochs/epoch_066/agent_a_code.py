def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_cells = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            self_cells.add((int(p[0]), int(p[1])))
    opp_cells = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            opp_cells.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                unclaimed.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = unclaimed if unclaimed else list(opp_cells) if opp_cells else list(self_cells)

    best_move = (0, 0)
    best_val = -10**18

    if candidates:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_to_opp = abs(ox - nx) + abs(oy - ny)
            d_self = abs(nx - sx) + abs(ny - sy)
            if unclaimed:
                best_t = -10**18
                for tx, ty in candidates:
                    if (tx, ty) == (nx, ny):
                        continue
                    d = abs(tx - nx) + abs(ty - ny)
                    gain = 6 * (max(0, 7 - (abs(tx - ox) + abs(ty - oy))))  # prefer far from opponent
                    score = -d + gain
                    if score > best_t:
                        best_t = score
                val = best_t + 0.5 * d_to_opp - 0.01 * d_self
            else:
                val = -abs(nx - ox) - abs(ny - oy)
                if (nx, ny) in opp_cells:
                    val += 4.5  # pressure opponent boundary
                if (nx, ny) in self_cells:
                    val -= 0.2
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]