def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (None, None))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    def inb(a, b):
        return 0 <= a < w and 0 <= b < h

    best = None
    best_sc = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue

            sc = 0
            if (nx, ny) in oppT:
                sc -= 2000
            if (nx, ny) in selfT:
                sc += 50
            if (nx, ny) in unclaimed:
                sc += 5000

            if ox is not None:
                d_opp = abs(nx - ox) + abs(ny - oy)
                sc += 12 * d_opp

            if unclaimed:
                phase = len(selfT) / max(1, w * h)
                want = -2 if phase < 0.35 else 1
                md = 10**9
                r = 6
                for ux, uy in unclaimed:
                    if abs(ux - x) > r or abs(uy - y) > r:
                        continue
                    d = abs(nx - ux) + abs(ny - uy)
                    if d < md:
                        md = d
                if md < 10**9:
                    sc += want * (-md)

            if sc > best_sc:
                best_sc = sc
                best = [dx, dy]

    if best is None:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best