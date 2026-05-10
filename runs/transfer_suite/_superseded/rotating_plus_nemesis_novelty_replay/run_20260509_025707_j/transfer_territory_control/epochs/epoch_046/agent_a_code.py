def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    my_pos = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_pos = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    myc = observation.get("self_territory_count", len(my_pos))
    opc = observation.get("opponent_territory_count", len(opp_pos))
    behind = myc < opc

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    targets = None
    if behind and opp_pos:
        targets = list(opp_pos)
    elif unclaimed:
        targets = list(unclaimed)
    elif my_pos:
        targets = list(my_pos)
    elif opp_pos:
        targets = list(opp_pos)
    else:
        targets = [(sx, sy)]

    def d2(x, y, tx, ty):
        dx = x - tx
        dy = y - ty
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = 0
        if (nx, ny) in my_pos:
            val += 20
        if (nx, ny) in opp_pos:
            val -= 50
        if (nx, ny) in unclaimed:
            val += 50 if not behind else 20

        # distance to chosen target(s)
        if targets:
            md = 10**18
            for tx, ty in targets:
                dd = d2(nx, ny, tx, ty)
                if dd < md:
                    md = dd
            val += (-md) * (1 if not behind else -0.6)

        # slight preference for staying within/near own territory
        if my_pos:
            near_my = 10**18
            for tx, ty in (my_pos if len(my_pos) < 25 else list(my_pos)[:25]):
                dd = d2(nx, ny, tx, ty)
                if dd < near_my:
                    near_my = dd
            val += 5 * (-near_my)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move