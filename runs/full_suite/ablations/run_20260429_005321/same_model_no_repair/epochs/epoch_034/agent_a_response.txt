def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    # Pick a target where we are relatively closer than the opponent.
    best_t = None
    best_key = None
    for tx, ty in resources:
        if (tx, ty) in obs:
            continue
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        # Key: prioritize (do-ds), then smaller ds, then smaller coordinates for determinism.
        key = (-(do - ds), ds, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    if best_t is None:
        tx, ty = resources[0]
    else:
        tx, ty = best_t

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        ns = man(nx, ny, tx, ty)
        no = man(ox, oy, tx, ty)
        # Prefer reducing distance to target; if we can't, try moves that hinder opponent's race.
        val = (ns - no) * 1000000 - ns * 1000 + (dx * 7 + dy * 3) - (tx * 0.01 + ty * 0.001)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]