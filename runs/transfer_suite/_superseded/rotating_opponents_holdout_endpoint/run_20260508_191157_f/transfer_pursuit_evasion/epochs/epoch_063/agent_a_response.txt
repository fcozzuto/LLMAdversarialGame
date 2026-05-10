def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = (observation.get("self_role") or "pursuer").lower()
    pursuer = role == "pursuer"

    cands = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2): 
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy
    def best_step(x, y, tx, ty, maximize):
        best = None; best_sc = None
        for dx, dy in cands:
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                continue
            d = cheb(nx, ny, tx, ty)
            sc = -d if not maximize else d
            if best is None or sc > best_sc:
                best_sc = sc; best = (dx, dy)
        return best if best is not None else (0, 0)

    def clearance(x, y):
        if not obs_set: return 2
        # Manhattan clearance to nearest obstacle, capped
        m = 100
        for ax, ay in obs_set:
            d = abs(x - ax) + abs(y - ay)
            if d < m: m = d
        return 0 if m == 0 else (m if m < 6 else 6)

    best_move = (0, 0)
    best_val = None
    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        # Opponent responds greedily on distance in opposite direction
        if pursuer:
            opp_dxdy = best_step(ox, oy, nx, ny, maximize=True)  # evader maximizes distance
            rx, ry = ox + opp_dxdy[0], oy + opp_dxdy[1]
            # Prefer smaller distance and safer placement near obstacles
            val = -cheb(nx, ny, rx, ry) + 0.05 * clearance(nx, ny)
            if best_val is None or val > best_val:
                best_val = val; best_move = (dx, dy)
        else:
            opp_dxdy = best_step(ox, oy, nx, ny, maximize=False)  # pursuer minimizes distance
            rx, ry = ox + opp_dxdy[0], oy + opp_dxdy[1]
            # As evader, maximize distance after pursuer response; also keep away from obstacles
            val = cheb(nx, ny, rx, ry) + 0.05 * clearance(nx, ny)
            if best_val is None or val > best_val:
                best_val = val; best_move = (dx, dy)

    return [best_move[0], best_move[1]]