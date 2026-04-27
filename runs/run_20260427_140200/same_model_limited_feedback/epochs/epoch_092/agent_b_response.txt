def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obst = set((x, y) for x, y in obstacles)
    dirs = [(0,0), (-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dsq(a,b,c,d):
        dx = a - c
        dy = b - d
        return dx*dx + dy*dy
    # Targets: nearest resource, and a "pressure" point toward intercepting opponent
    if resources:
        r_near = min(resources, key=lambda p: dsq(p[0], p[1], sx, sy))
        rr_near = min(resources, key=lambda p: dsq(p[0], p[1], ox, oy))
    else:
        r_near = (w//2, h//2)
        rr_near = (w//2, h//2)
    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            nx, ny = sx, sy  # engine keeps in place; emulate to score consistently
        # Main: get closer to our nearest resource
        dres = dsq(nx, ny, r_near[0], r_near[1])
        # Secondary: keep distance from opponent to avoid losing trades
        dop = dsq(nx, ny, ox, oy)
        # Interference: move toward reducing opponent's access (increase their distance to their nearest resource)
        dopres = dsq(ox, oy, rr_near[0], rr_near[1])
        dopres_after = dsq(ox, oy, rr_near[0], rr_near[1])  # opponent doesn't move now; use our "capture line" as proxy
        # Proxy capture: if we are on/near the straight path to their nearest resource, add bonus
        tx, ty = rr_near
        # Manhattan-ish alignment score (diagonal allowed)
        align = -(abs(nx - tx) + abs(ny - ty)) + (abs(sx - tx) + abs(sy - ty))
        # Obstacle-aware: slight penalty for being adjacent to obstacles (encourage safer corridors)
        adj_obs = 0
        for adx, ady in dirs[1:]:
            px, py = nx + adx, ny + ady
            if inb(px, py) and (px, py) in obst:
                adj_obs += 1
        v = (-dres) + (0.12 * dop) + (0.08 * align) - (0.05 * adj_obs)
        # Deterministic tie-break: prefer moves with lexicographic (dx,dy)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]