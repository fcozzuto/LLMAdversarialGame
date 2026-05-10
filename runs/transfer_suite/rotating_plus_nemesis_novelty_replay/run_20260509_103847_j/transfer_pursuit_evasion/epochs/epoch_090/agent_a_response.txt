def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role) or ("runner" in role)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if is_evader:
        # Prefer moves that increase distance in Chebyshev metric; tie-break toward farthest corner.
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        far_corner = max(corners, key=lambda c: abs(c[0]-ox)+abs(c[1]-oy))
        fc_x, fc_y = far_corner

        def dist_after(nx, ny):
            return max(abs(nx-ox), abs(ny-oy)), abs(fc_x-nx)+abs(fc_y-ny)

        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                d1, d2 = dist_after(nx, ny)
                key = (d1, d2, -abs(nx-ox)-abs(ny-oy))  # deterministic tie-break
                if best_key is None or key > best_key:
                    best_key = key
                    best = [dx, dy]
        return best if best is not None else [0, 0]
    else:
        # Pursuer: minimize distance; secondary tie-break toward moving along the straight line to opponent.
        def dist_after(nx, ny):
            return max(abs(nx-ox), abs(ny-oy))

        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                d = dist_after(nx, ny)
                # Prefer step that reduces dx/ dy offsets toward opponent (deterministic).
                align = - (abs((nx - ox)) + abs((ny - oy)))
                key = (d, align, dx, dy)
                if best_key is None or key < best_key:
                    best_key = key
                    best = [dx, dy]
        return best if best is not None else [0, 0]