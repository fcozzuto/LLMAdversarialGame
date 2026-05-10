def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    # Pick a target resource that we can reach sooner than the opponent (or at least contest strongly)
    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # adv > 0 means we are closer
        adv = do - ds
        # Prefer grabbing in/near opponent row to contest (shadow/sweep-like behavior)
        row_contest = 1 if ry == oy else 0
        # Small tie-breaker: prefer nearer resources when adv ties
        key = (-adv - 0.25 * row_contest, ds + (0.01 if ry != oy else 0), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_mkey = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        ds_next = abs(tx - nx) + abs(ty - ny)
        ds_now = abs(tx - sx) + abs(ty - sy)

        # Opponent pressure: discourage moves that bring opponent closer to our target relative to us
        do_here = abs(tx - nx) + abs(ty - ny)  # our distance after move
        do_opp_next = abs(tx - ox) + abs(ty - oy)  # opponent doesn't move, but keep contest metric stable

        # Resource pickup immediate heuristic
        on_resource = 1 if (nx, ny) in resources else 0

        # Prefer reducing distance to target; if we can't reduce, still allow contest by not moving away too much.
        move_toward = ds_now - ds_next  # positive is good
        # If we are contesting opponent's row, prefer also matching that row movement when possible.
        row_bonus = 1 if ty == oy and ny == oy else 0

        mkey = (-(on_resource * 1000 + move_toward * 10 + row_bonus * 2),
                (do_opp_next - do_here),  # larger means opponent farther; smaller is worse
                ds_next, abs(nx - ox) + abs(ny - oy), nx, ny)

        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]