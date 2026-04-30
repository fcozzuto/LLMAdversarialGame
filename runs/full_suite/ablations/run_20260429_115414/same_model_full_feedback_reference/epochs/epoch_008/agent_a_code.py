def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)
    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2 and (p[0], p[1]) not in obs]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def legal(nx, ny): return inb(nx, ny) and (nx, ny) not in obs
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    best = None
    best_dxdy = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): 
            continue
        opp_d = cheb(nx, ny, ox, oy)
        if res:
            my_d = None
            for rx, ry in res:
                d = cheb(nx, ny, rx, ry)
                if my_d is None or d < my_d:
                    my_d = d
            # Prefer smaller distance to resources; slightly prefer being farther from opponent.
            val = (-my_d * 1000) + opp_d
        else:
            val = opp_d
        if best is None or val > best or (val == best and (dx, dy) < best_dxdy):
            best = val
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]