def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Deterministic tie-breaking: prefer smaller dx, then smaller dy
    moves.sort(key=lambda t: (t[0], t[1]))

    if not resources:
        # No resources visible: move to reduce distance to opponent's corner opposite direction
        tx, ty = (w - 1, h - 1) if sx < w/2 else (0, 0)
        target = (tx, ty)
    else:
        # Strategy change: alternate between nearest and farthest resource to vary pursuit pattern
        nearest = observation["turn_index"] % 2 == 0
        if nearest:
            target = min(resources, key=lambda p: abs(p[0]-sx) + abs(p[1]-sy))
        else:
            target = max(resources, key=lambda p: abs(p[0]-sx) + abs(p[1]-sy))

    best = None
    best_util = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dt = abs(target[0] - nx) + abs(target[1] - ny)
        do = abs(ox - nx) + abs(oy - ny)
        # Primary: get closer to target; Secondary: keep distance from opponent slightly
        util = -dt + (0.001 * do)
        if util > best_util:
            best_util = util
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]