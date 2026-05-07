def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def sign(z):
        return 0 if z == 0 else (1 if z > 0 else -1)

    # Prefer resources we can reach strictly earlier; if none, pick the least contested.
    best = None
    best_key = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # win_flag: 1 if we can arrive first, else 0
        win_flag = 1 if ds < do else 0
        # minimize our distance, maximize opponent delay; avoid ties
        key = (win_flag,
               -do,              # smaller opponent distance is worse; so more negative is worse => use -do in max by negating below
               -(do - ds),      # bigger separation in our favor is better
               -ds,             # closer is better (via max on -ds)
               rx, ry)
        # Convert to deterministic max by comparing score tuple directly
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    desired_dx = sign(tx - sx)
    desired_dy = sign(ty - sy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_mkey = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        # Move scoring: go toward target, avoid giving opponent a quicker path, prefer alignment to desired.
        d_self = cheb(nx, ny, tx, ty)
        d_opp_after = cheb(ox, oy, tx, ty)
        # If opponent is already as close or closer, try to reduce our distance aggressively (denier mindset).
        contested = 1 if d_opp_after <= d_self else 0
        align = -abs(dx - desired_dx) - abs(dy - desired_dy)
        # also keep within bounds if provided; otherwise assume engine clamps/handles
        w = observation.get("grid_width", 8)
        h = observation.get("grid_height", 8)
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        mkey = (1 - contested, -d_self, align, dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move