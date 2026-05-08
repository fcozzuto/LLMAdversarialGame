def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    def step_toward(tx, ty):
        best = [0, 0]
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            # Prefer to approach target, then to move away from opponent, then deterministically by dx,dy
            key = (abs(tx - nx) + abs(ty - ny), -(abs(ox - nx) + abs(oy - ny)), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        return best
    best_res = None
    best_key = None
    for rx, ry in res:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        key = (do - ds, ds, rx, ry)  # maximize lead over opponent; then nearer; then deterministic
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)
    tx, ty = best_res
    return step_toward(tx, ty)