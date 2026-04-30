def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))
    res_count = observation.get('remaining_resource_count', len(resources))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def best_target():
        if not resources: return [sx, sy]
        # Prefer resources that are closer to us and farther from opponent (denial)
        # If few resources remain, prioritize direct approach.
        k = 0.9 if res_count > 6 else 0.2
        best = None
        for rx, ry in resources:
            du = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            val = du - k * do
            if best is None or val < best[0]:
                best = [val, rx, ry]
        return [best[1], best[2]]

    tx, ty = best_target()

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Encourage moving onto/near target, and avoid giving opponent easy access.
        d_t = abs(tx - nx) + abs(ty - ny)
        d_op = abs(ox - nx) + abs(oy - ny)
        # Small tie-break to reduce oscillation: prefer staying closer to current target line.
        dx_target = 0 if tx == sx else (1 if tx > sx else -1)
        dy_target = 0 if ty == sy else (1 if ty > sy else -1)
        align = - (abs(dx - dx_target) + abs(dy - dy_target))
        # If opponent is adjacent to the target, increase urgency to get it first.
        opp_to_t = abs(tx - ox) + abs(ty - oy)
        urgency = 2.0 if opp_to_t <= 2 else 0.0
        on_resource = 1.5 if [nx, ny] in resources else 0.0
        score = (-d_t) + 0.05 * d_op + align + urgency + on_resource
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all moves blocked, stay still.
    return best_move if best_move in ([dx, dy] for dx, dy in moves) else [0, 0]