def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        # try alternate single-step moves (deterministic order)
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                if a == 0 and b == 0:
                    continue
                nx, ny = sx + a, sy + b
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    return [a, b]
        return [0, 0]

    if resources:
        tx, ty = resources[0]
        return step_towards(tx, ty)

    candidates = []

    # Prefer unclaimed cells adjacent to our territory (frontier expansion)
    if self_terr:
        for x, y in self_terr:
            for dx, dy in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                    d = abs(nx - sx) + abs(ny - sy)
                    candidates.append((0, d, nx, ny))  # type 0 = frontier

    # If none, target unclaimed near center to grow control
    if not candidates:
        for (ux, uy) in unclaimed:
            if (ux, uy) in obstacles:
                continue
            d = abs(ux - (w - 1) / 2.0) + abs(uy - (h - 1) / 2.0) + 0.25 * (abs(ux - sx) + abs(uy - sy))
            candidates.append((1, d, ux, uy))  # type 1 = center-ish

    # If still none (rare), target adjacent to opponent to enable flipping
    if not candidates:
        if opp_terr:
            for x, y in opp_terr:
                for dx, dy in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in self_terr:
                        d = abs(nx - sx) + abs(ny - sy)
                        candidates.append((2, d, nx, ny))  # type 2 = attack/approach

    if not candidates:
        return [0, 0]

    candidates.sort()
    _, _, tx, ty = candidates[0]
    return step_towards(tx, ty)