def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def neigh_unclaimed_count(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and ((nx, ny) in unclaimed or (nx, ny) in opp_terr):
                    c += 1
        return c

    # Choose a target unclaimed cell (and prefer ones not too close to opponent)
    target = None
    best_td = 10**9
    for tx, ty in unclaimed:
        if (tx, ty) in obstacles:
            continue
        td = manh(sx, sy, tx, ty)
        od = manh(ox, oy, tx, ty)
        # Prefer closer but also with some distance from opponent
        key = (td * 2 - min(od, 6))
        if key < best_td or (key == best_td and (tx, ty) < target):
            best_td = key
            target = (tx, ty)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        status = 0
        if (nx, ny) in unclaimed:
            status = 4
        elif (nx, ny) in opp_terr:
            status = 3
        elif (nx, ny) in self_terr:
            status = 1

        frontier = neigh_unclaimed_count(nx, ny)
        # Pull toward target; also avoid immediate proximity to opponent
        if target is not None:
            dist_to_target = manh(nx, ny, target[0], target[1])
        else:
            dist_to_target = 0
        dist_to_opp = manh(nx, ny, ox, oy)

        score = status * 100 + frontier * 12 - dist_to_target * 2 + min(dist_to_opp, 6) * 3
        # tiny deterministic bias toward staying within/near territory
        if (nx, ny) in self_terr:
            score += 1

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]