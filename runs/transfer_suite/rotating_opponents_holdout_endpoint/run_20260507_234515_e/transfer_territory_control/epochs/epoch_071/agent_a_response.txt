def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or [0, 0])
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not inb(sx, sy):
        sx, sy = 0, 0
    if not unclaimed:
        # Defensive: head toward border cell that minimizes opponent distance if stuck
        if opp_terr:
            tx, ty = min(self_terr or [(sx, sy)], key=lambda p: abs(p[0] - next(iter(opp_terr))[0]) + abs(p[1] - next(iter(opp_terr))[1]))
        else:
            tx, ty = sx, sy
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    frontier = []
    if self_terr:
        for x, y in unclaimed:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in self_terr:
                    frontier.append((x, y))
                    break
    candidates = frontier if frontier else list(unclaimed)

    # Deterministic scoring: prioritize frontier, then far from opponent, then close to self.
    opp_list = list(opp_terr)
    def best_score(t):
        tx, ty = t
        d_self = abs(tx - sx) + abs(ty - sy)
        if opp_list:
            d_opp = min(abs(tx - ox) + abs(ty - oy) for ox, oy in opp_list)
        else:
            d_opp = 99
        # Prefer frontier (if frontier exists), then higher d_opp, then lower d_self.
        return (0 if frontier else 1, -d_opp, d_self, tx, ty)

    target = min(candidates, key=best_score)
    tx, ty = target

    # Greedy one-step toward target with obstacle-avoidance and tie-breaks.
    def try_move(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    primary = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if try_move(nx, ny):
            primary.append((abs((tx) - nx) + abs((ty) - ny), abs(dx) + abs(dy), dx, dy))
    primary.sort()
    if primary:
        return [int(primary[0][2]), int(primary[0][3])]
    return [0, 0]