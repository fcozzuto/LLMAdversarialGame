def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    opc = observation.get("opponent_territory_count", len(opp_set))
    myc = observation.get("self_territory_count", len(self_set))
    behind = myc < opc

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_cells(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    yield nx, ny

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_pos = observation["opponent_position"]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**9, (0, 0))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = 0
        if (nx, ny) in opp_set:
            val += 16 if behind else 12
            val += 6 - min(6, manh((nx, ny), opp_pos))
        elif (nx, ny) in unclaimed:
            val += 8 if behind else 6
            val += 4 - min(4, manh((nx, ny), opp_pos))
        elif (nx, ny) in self_set:
            val += 2
        # Edge/contested bias: prefer stepping into frontier between unclaimed and opponent
        if (nx, ny) not in self_set:
            edge = 0
            adj_un = 0
            for ax, ay in adj_cells(nx, ny):
                if (ax, ay) in opp_set:
                    edge += 1
                if (ax, ay) in unclaimed:
                    adj_un += 1
            val += 3 * edge + (2 if adj_un else 0)
            if adj_un and not edge:
                val -= 1
        # Avoid getting stuck next to opponent unless we can flip/claim next
        adj_opp = any((ax, ay) in opp_set for ax, ay in adj_cells(nx, ny))
        if adj_opp and (nx, ny) not in opp_set:
            val -= 3 if behind else 1

        # Micro-aim: keep pressure toward opponent side
        val += -0.05 * manh((nx, ny), opp_pos)

        if val > best[0]:
            best = (val, (dx, dy))
    return [int(best[1][0]), int(best[1][1])]