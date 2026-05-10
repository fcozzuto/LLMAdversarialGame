def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    path = observation.get("self_path") or []
    recent = set()
    for p in path[-7:]:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            recent.add((int(p[0]), int(p[1])))

    adj8 = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a-c) + abs(b-d)

    best = (None, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in opp_terr:
            val += 120
        elif (nx, ny) in unclaimed:
            val += 25
        elif (nx, ny) in self_terr:
            val += 8
        else:
            val += 3

        # Encourage moves that touch opponent territory (likely to flip/advance frontier)
        touch = 0
        for adx, ady in adj8:
            q = (nx + adx, ny + ady)
            if q in opp_terr:
                touch += 1
        val += 8 * touch

        # Prefer moving toward opponent
        val -= man(nx, ny, ox, oy) * 1.2

        # Reduce loops
        if (nx, ny) in recent:
            val -= 18

        # Mild preference to stay if equal (deterministic tie-break via fixed move ordering)
        if val > best[1]:
            best = ((dx, dy), val)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]