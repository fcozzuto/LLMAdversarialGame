def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    remaining = observation.get("remaining_resource_count", len(resources))

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def min_dist_to_resources(x, y):
        if not resources:
            return 10**9
        md = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < md: md = d
            if md == 0: break
        return md

    cx, cy = (w - 1) // 2, (h - 1) // 2
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    has_res = bool(resources) and remaining > 0
    best_move = (0, 0, sx, sy)
    best_val = -10**18

    myD0 = cheb(sx, sy, ox, oy)
    for dx, dy, nx, ny in legal:
        if has_res:
            d_my = min_dist_to_resources(nx, ny)
            # if stepping onto a resource, strongly prefer (deterministic capture)
            on_res = 1 if any(nx == rx and ny == ry for rx, ry in resources) else 0
            d_opp = min_dist_to_resources(ox, oy)
            # "contested" heuristic: if opponent is already closer, prioritize distancing from opponent
            d_opp_next = min_dist_to_resources(ox + dx, oy + dy) if ok(ox + dx, oy + dy) else min_dist_to_resources(ox, oy)
            opp_d = cheb(nx, ny, ox, oy)
            v = 0.0
            v += 1000.0 * on_res
            v -= 7.0 * d_my
            v += 0.6 * cheb(nx, ny, cx, cy)
            v += 0.3 * myD0 - 0.35 * opp_d
            v += 1.2 * (d_opp - d_my)  # go where we are relatively advantaged
            v += 0.2 * (d_opp_next - d_opp)  # small pressure if opponent can be delayed
        else:
            # no resources: drift to center and avoid being too close to opponent
            opp_d = cheb(nx, ny, ox, oy)
            v = -cheb(nx, ny, cx, cy) + 0.2 * (opp_d)
        if v > best_val or (v == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = v
            best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]