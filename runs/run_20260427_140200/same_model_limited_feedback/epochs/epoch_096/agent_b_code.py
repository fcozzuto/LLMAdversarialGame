def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_val = -10**18

    # If no resources, drift away from opponent while avoiding obstacles
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            opp_d = cheb(nx, ny, ox, oy)
            obs_pen = 0
            for ax in (-1,0,1):
                for ay in (-1,0,1):
                    if (nx+ax, ny+ay) in obstacles:
                        obs_pen -= 2
            val = opp_d + obs_pen
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Pick the resource that maximizes our advantage from the NEXT position
        best_res = None
        best_res_val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; otherwise deny by being the "best alternative"
            v = (od - sd) * 10 - sd
            # If opponent is already very close, strongly prefer other resources
            if od <= 1 and sd > 1:
                v -= 50
            if v > best_res_val:
                best_res_val = v
                best_res = (rx, ry)

        rx, ry = best_res
        sd = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)

        # Obstacle and edge safety
        obs_pen = 0
        for ax in (-1,0,1):
            for ay in (-1,0,1):
                if (nx+ax, ny+ay) in obstacles:
                    obs_pen -= 3
        # Mild collision-avoidance with opponent
        opp_d = cheb(nx, ny, ox, oy)
        block_bonus = 0
        if opp_d <= 1:
            # If we can meet or block, prefer it
            block_bonus += 8
            if sd > 1:
                block_bonus -= 6

        val = best_res_val + obs_pen + (opp_d * 0.2) + block_bonus
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]