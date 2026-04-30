def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    res = []
    for r in resources:
        if r and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
    rem = int(observation.get("remaining_resource_count", len(res) if res else 0) or 0)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def best_opp_next(px, py):
        moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
        best = None; best_val = None
        target = None
        if res and rem > 0:
            target = min(res, key=lambda t: cheb(px, py, t[0], t[1]))
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not ok(nx, ny): 
                continue
            if target is not None:
                val = cheb(nx, ny, target[0], target[1])  # greedy toward nearest resource
                # slight preference to keep distance from us
                val += 0.25 * cheb(nx, ny, sx, sy)
            else:
                # drift away from us
                val = -cheb(nx, ny, sx, sy)
                val += 0.1 * (nx * 0 + ny * 0)
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy, nx, ny)
        return best

    opp_next = best_opp_next(ox, oy)
    opp_cell = (opp_next[2], opp_next[3]) if opp_next else None

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # core objectives: get closer to resources, keep away from opponent
        if res and rem > 0:
            dres = min(cheb(nx, ny, rx, ry) for rx, ry in res)
        else:
            dres = 3  # neutral
        d_opp = cheb(nx, ny, ox, oy)

        # interaction: avoid stepping into opponent's likely next cell
        avoid_opp = 0
        if opp_cell is not None and (nx, ny) == opp_cell:
            avoid_opp = 50

        # obstacle proximity penalty
        obst_near = 0
        for bx, by in blocked:
            if abs(bx - nx) <= 1 and abs(by - ny) <= 1:
                obst_near += 1

        # slight tie-breaker: prefer forward toward center
        center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = cheb(nx, ny, int(center_x), int(center_y)) * 0.01

        score = (dres * 1.4) - (d_opp * 1.2) + obst_near * 0.6 + avoid_opp + center_bias
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]