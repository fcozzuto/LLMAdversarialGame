def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    selfT, oppT, unclaimed = set(), set(), set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    # Prefer moves that (a) avoid obstacles, (b) land on opponent/unclaimed near opponent
    opp_front = set()
    if oppT:
        for x, y in oppT:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                        opp_front.add((nx, ny))

    targets = []
    if opp_front:
        targets = list(opp_front)
    elif unclaimed:
        targets = list(unclaimed)

    def best_target_dist(nx, ny):
        if not targets:
            return 10**9
        bd = 10**9
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < bd:
                bd = d
        return bd

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break: fixed move order above
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in oppT:
            gain = 100000
        elif (nx, ny) in unclaimed:
            gain = 50000
        elif (nx, ny) in selfT:
            gain = 1000
        else:
            gain = 0
        bd = best_target_dist(nx, ny)
        # Secondary preference: move toward opponent generally if no front
        odx = abs(nx - (observation.get("opponent_position") or [W - 1, H - 1])[0])
        ody = abs(ny - (observation.get("opponent_position") or [W - 1, H - 1])[1])
        threat = odx + ody
        score = gain - bd * 10 - threat
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]