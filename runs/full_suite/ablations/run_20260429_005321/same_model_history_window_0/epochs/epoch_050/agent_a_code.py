def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (-(10**9), 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h): 
                    continue
                if (nx, ny) in obstacles: 
                    continue
                d = abs(nx - tx) + abs(ny - ty)
                if -d > best[0]:
                    best = (-d, dx, dy)
        return [best[1], best[2]]
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    def closest_dist(px, py):
        c = 10**9
        for rx, ry in resources:
            d = abs(px - rx) + abs(py - ry)
            if d < c: 
                c = d
        return c
    opp_cd = closest_dist(ox, oy)
    best_val, best_dx, best_dy = -(10**18), 0, 0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles: 
                continue
            my_cd = closest_dist(nx, ny)
            # Heuristic: prioritize getting to resources; also prefer moves that reduce opponent lead.
            value = (-my_cd) + 0.6 * (opp_cd - my_cd)
            # Small tie-breakers: prefer staying away from walls and corners slightly.
            wall_bonus = - (min(nx, w-1-nx) < 1 or min(ny, h-1-ny) < 1) * 0.1
            value += wall_bonus
            if value > best_val:
                best_val, best_dx, best_dy = value, dx, dy
            elif value == best_val:
                # Deterministic tie-break preference order: diagonal, then straight, then stay
                pref = (abs(dx) + abs(dy) == 2, abs(dx) + abs(dy) == 1, abs(dx) + abs(dy) == 0)
                bpref = (abs(best_dx) + abs(best_dy) == 2, abs(best_dx) + abs(best_dy) == 1, abs(best_dx) + abs(best_dy) == 0)
                if pref > bpref:
                    best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]