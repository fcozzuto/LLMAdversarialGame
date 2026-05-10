def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    ox, oy = observation.get("opponent_position", (x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    neigh_opp = 0
    for dx, dy in dirs:
        if dx == 0 and dy == 0:
            continue
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in oppT:
            neigh_opp += 1

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        score = 0.0
        if (nx, ny) in oppT:
            score += 9.0  # immediate steal/flip pressure

        if (nx, ny) in selfT:
            score += 0.5
        elif (nx, ny) in unclaimed:
            score += 3.0
        else:
            score += 0.0

        # Frontier pressure: prefer getting closer to nearest unclaimed, but cut through toward opponent when attacking.
        if unclaimed:
            md = 10**9
            for tx, ty in unclaimed:
                d = dist(nx, ny, tx, ty)
                if d < md:
                    md = d
            score += -1.2 * md

        # Tactical: avoid walking into immediate opponent-adjacent traps unless we can steal now.
        opp_adj = 0
        for ddx, ddy in dirs:
            if ddx == 0 and ddy == 0:
                continue
            ax, ay = nx + ddx, ny + ddy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in oppT:
                opp_adj += 1
        if opp_adj > 0 and (nx, ny) not in oppT:
            score += -1.0 * opp_adj

        # Keep some separation from opponent unless stealing.
        d_now = dist(x, y, ox, oy)
        d_next = dist(nx, ny, ox, oy)
        if (nx, ny) in oppT:
            score += 0.4 * (d_next - d_now)
        else:
            score += 0.35 * (d_next - d_now)

        # Mild bias toward progressing away from start corner to cover more area deterministically.
        if (x, y) == (0, 0):
            score += 0.05 * (nx + ny)
        elif (x, y) == (w - 1, h - 1):
            score += 0.05 * ((w - 1 - nx) + (h - 1 - ny))

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move