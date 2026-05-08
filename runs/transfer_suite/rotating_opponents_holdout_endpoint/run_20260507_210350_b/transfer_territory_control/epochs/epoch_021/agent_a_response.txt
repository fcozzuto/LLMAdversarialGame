def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key, []) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")

    # Decide focus deterministically
    self_cnt = int(observation.get("self_territory_count", len(self_terr)))
    opp_cnt = int(observation.get("opponent_territory_count", len(opp_terr)))
    favor_attack = self_cnt < opp_cnt

    # Quick target preference: closest unclaimed; if none, boundary against opponent
    targets = list(unclaimed)
    if not targets:
        # Prefer cells adjacent to opponent territory to create flipping opportunities
        targets = []
        for (x, y) in opp_terr:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and (nx, ny) not in self_terr:
                    targets.append((nx, ny))
        if not targets:
            targets = list(opp_terr) if favor_attack else list(unclaimed) if unclaimed else [(w // 2, h // 2)]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    nearest_target = min(targets, key=lambda p: manh((sx, sy), p))

    # Fixed move ordering for determinism
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue

        # If obstacle, engine keeps us in place; reflect that with nx,ny -> sx,sy
        if (nx, ny) in obstacles:
            nx, ny = sx, sy

        in_unclaimed = (nx, ny) in unclaimed
        in_self = (nx, ny) in self_terr
        in_opp = (nx, ny) in opp_terr

        # Base desirability
        score = 0
        if in_unclaimed:
            score += 200
        if in_opp:
            score += 120 if favor_attack else 70
        if in_self:
            score -= 5

        # Distance shaping
        # Always move toward nearest target; if attacking, also reduce distance to opponent
        score -= 2 * manh((nx, ny), nearest_target)
        if favor_attack:
            score -= manh((nx, ny), (ox, oy))

        # Encourage edge advancement subtly (territory control tends to swing around space)
        score += 3 * (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)

        key = (-score, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]