def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    res = observation.get("resources", [])

    obs_set = set((p[0], p[1]) for p in obstacles)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def best_step(tx, ty):
        best = None
        best_d = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs_set:
                continue
            d = abs(tx - nx) + abs(ty - ny)
            # Tie-breakers: prefer getting closer; then deterministic direction preference
            cand = (d, abs(tx-(sx+dx))+abs(ty-(sy+dy)), dx, dy)
            if d < best_d:
                best_d = d
                best = [dx, dy]
            elif d == best_d and best is not None:
                if cand < (best_d, best_d, best[0], best[1]):
                    best = [dx, dy]
        return best if best is not None else [0, 0]

    if not res:
        # With no visible resources, move toward opponent to contest
        return best_step(ox, oy)

    # Choose nearest resource; deterministic tie-break by coordinates
    tx, ty = sorted(res, key=lambda p: (abs(p[0]-sx)+abs(p[1]-sy), p[0], p[1]))[0]

    # If we can "win" the closest resource race by being nearer than opponent, go straight for it
    myd = abs(tx - sx) + abs(ty - sy)
    opd = abs(tx - ox) + abs(ty - oy)
    if opd < myd:
        # Consider next closest to avoid giving opponent an easy claim
        tx, ty = sorted(res, key=lambda p: (abs(p[0]-ox)+abs(p[1]-oy), abs(p[0]-sx)+abs(p[1]-sy), p[0], p[1]))[0]
    return best_step(tx, ty)