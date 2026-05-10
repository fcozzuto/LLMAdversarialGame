def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    self_territory = observation.get("self_territory") or []
    opp_territory = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    def toset(lst):
        s = set()
        for p in lst:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    ob = toset(obstacles)
    us = toset(self_territory)
    os = toset(opp_territory)
    uc = toset(unclaimed)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def adj8(x, y, s):
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in s:
                return True
        return False

    best_t = None
    best_v = -10**18
    for tx, ty in uc:
        if (tx, ty) in ob:
            continue
        d = abs(tx - ax) + abs(ty - ay)
        score = -d
        if adj8(tx, ty, us):
            score += 3
        if adj8(tx, ty, os):
            score += 6
        if (tx, ty) == (ax, ay):
            score += 1
        if score > best_v:
            best_v = score
            best_t = (tx, ty)

    # If no unclaimed, contest near opponent territory; otherwise stay.
    if best_t is None:
        if os:
            ox, oy = min(os, key=lambda p: abs(p[0] - ax) + abs(p[1] - ay))
            best_t = (ox, oy)
        else:
            return [0, 0]

    tx, ty = best_t
    best_m = (0, 0)
    best_mv = -10**18
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in ob:
            continue
        d2 = abs(tx - nx) + abs(ty - ny)
        mv = -d2
        if (nx, ny) in uc:
            mv += 12
        if (nx, ny) in os:
            mv += 10
        if (nx, ny) in us:
            mv += 1
        # mild preference to not immediately get stuck: discourage moving away from target
        if dx == 0 and dy == 0:
            mv -= 1
        if mv > best_mv:
            best_mv = mv
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]